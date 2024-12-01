import unittest
from io import BytesIO
from app import myapp_obj, db
from app.models import User

class AuthTestCase(unittest.TestCase):

    def setUp(self):
        # Initialize the app and test client
        self.app = myapp_obj
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory database
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()  # Create tables for testing

    def tearDown(self):
        # Cleanup database after each test
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_registration(self):
        """Test user registration with valid and invalid data."""
        # Valid registration
        response = self.client.post('/register', data={
            'reg_role': 'student',  # Select a valid role from the dropdown
            'fname': 'John',
            'lname': 'Doe',
            'username': 'testuser',
            'email': 'test@sjsu.edu',
            'password': 'password123',
            'confirm': 'password123',
            #dircet image path instead of fake data
            'file': (BytesIO(b"fake image data"), 'testfile.jpg')  # Simulate file upload
        }, follow_redirects=True)

        # Check if redirected to login or success page
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'To register, click the Register button', response.data)

        '''' treat it in another function instead of tesitng here as well, use variables to pass value in different test function''''
        # Verify user was added to the database
        with self.app.app_context():
            user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, 'test@sjsu.edu')
            self.assertTrue(user.check_password('password123'))

        # Duplicate username
        response = self.client.post('/register', data={
            'reg_role': 'student',
            'fname': 'Jane',
            'lname': 'Doe',
            'username': 'testuser',  # Duplicate username
            'email': 'jane@sjsu.edu',
            'password': 'password123',
            'confirm': 'password123',
            'file': (BytesIO(b"fake image data"), 'testfile2.jpg')
        }, follow_redirects=True)
        self.assertIn(b'That username already exists', response.data)

        # Invalid role
        response = self.client.post('/register', data={
            'reg_role': 'invalidrole',  # Invalid role
            'fname': 'Alice',
            'lname': 'Smith',
            'username': 'newuser',
            'email': 'alice@sjsu.edu',
            'password': 'password123',
            'confirm': 'password123',
            'file': (BytesIO(b"fake image data"), 'testfile3.jpg')
        }, follow_redirects=True)
        self.assertIn(b'Invalid role!', response.data)

        # Missing file
        response = self.client.post('/register', data={
            'reg_role': 'student',
            'fname': 'Alice',
            'lname': 'Smith',
            'username': 'alice',
            'email': 'alice@sjsu.edu',
            'password': 'password123',
            'confirm': 'password123'
            # File is missing
        }, follow_redirects=True)
        self.assertIn(b'This field is required.', response.data)

        # Click "Sign In" button
        response = self.client.post('/register', data={
            'sign': True  # Simulate clicking the "Sign In" button
        }, follow_redirects=True)
        self.assertIn(b'<title>Login</title>', response.data)  # Ensure the login page loads

    def test_user_login(self):
        """#Test user login with valid and invalid credentials.
        # Add a user directly to the database
        with self.app.app_context():
            user = User(
                username='testuser',
                email='test@sjsu.edu',
                fname='John',
                lname='Doe',
                file='testfile.jpg',
                data=b'fake image data',
                reg_role='student',
                act_role='student',
                rfid='123456789'
            )
            user.set_password('password123')  # Hash the password
            db.session.add(user)
            db.session.commit()
        """
        # Valid login (without follow_redirects)
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password123',
            'email': 'test@sjsu.edu',
            'submit': True  # Simulate clicking the "Sign In" button
        }, follow_redirects=False)

        # Check for redirect
        self.assertEqual(response.status_code, 200)  # 302 indicates redirect
        self.assertIn('/index', response.headers['Location'])  # Check redirect target

        # Valid login (with follow_redirects)
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password123',
            'email': 'test@sjsu.edu',
            'submit': True  # Simulate clicking the "Sign In" button
        }, follow_redirects=True)

        # Check the redirected page content
        self.assertEqual(response.status_code, 200)  # Successful response after redirect
        self.assertIn(b'Welcome', response.data)  # Assuming the home page contains 'Welcome'

        # Invalid password
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword',
            'email': 'test@sjsu.edu',
            'submit': True  # Simulate clicking the "Sign In" button
        }, follow_redirects=True)
        self.assertIn(b'Incorrect password!', response.data)

        # Non-existent username
        response = self.client.post('/login', data={
            'username': 'nonexistent',
            'password': 'password123',
            'email': 'test@sjsu.edu',
            'submit': True  # Simulate clicking the "Sign In" button
        }, follow_redirects=True)
        self.assertIn(b'That username is not registered!', response.data)


if __name__ == '__main__':
    unittest.main()
