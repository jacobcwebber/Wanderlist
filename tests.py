import os
import unittest
from app import app, db
from app.models import User, Destination, Country, Region, Continent

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('TESTING_DATABASE_URL')
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        user = User(username='mackenzie')
        user.set_password('password')
        self.assertFalse(user.check_password('passw0rd'))
        self.assertTrue(user.check_password('password'))

    def test_avatar(self):
        user = User(username='jacob', email='jacob@example.com')
        self.assertEqual(user.avatar(128), ('https://www.gravatar.com/avatar/'
                                         '7a140783d558a1814a38a3bf7ed5f204'
                                         '?d=identicon&s=128'))
    
    def test_explored_and_favorites(self):
        cont = Continent(name='Asia', id=1)
        region = Region(name='Southeast Asia', id=1, cont_id=1)
        country = Country(name='Myanmar', id=1, region_id=1)
        dest = Destination(name='Bagan', id=1, country_id=1)
        user = User(username='jacob')

        db.session.add_all([cont, region, country, dest, user])
        db.session.commit()

        self.assertEqual(user.explored_dests.all(), [])
        self.assertEqual(user.favorited_dests.all(), [])

        user.add_explored(dest)
        user.add_favorite(dest)
        db.session.commit()
        self.assertTrue(user.has_explored(dest))
        self.assertTrue(user.has_favorited(dest))
        self.assertEqual(user.explored_dests.first().name, 'Bagan')
        self.assertEqual(user.favorited_dests.first().name, 'Bagan')
        self.assertEqual(dest.explored_users.first().username, 'jacob')
        self.assertEqual(dest.favorited_users.first().username, 'jacob')

        user.remove_explored(dest)
        user.remove_favorite(dest)
        db.session.commit()

if __name__ == '__main__':
    unittest.main(verbosity=2)