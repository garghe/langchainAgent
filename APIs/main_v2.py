from flask import Flask, request, jsonify
import sqlite3
import logging

logging.basicConfig(level=logging.DEBUG)  # Set the logging level
logger = logging.getLogger(__name__)      # Create a logger instance

app = Flask(__name__)

# Database initialization
def init_db():
    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookings
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         firstname TEXT NOT NULL,
         lastname TEXT NOT NULL,
         num_people INTEGER NOT NULL,
         booking_datetime TEXT NOT NULL)
    ''')
    conn.commit()
    conn.close()


# Initialize database on startup
init_db()


def dict_factory(cursor, row):
    """Convert database rows to dictionaries"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.route('/book', methods=['GET', 'POST', 'PUT'])
def handle_booking():
    conn = sqlite3.connect('bookings.db')
    conn.row_factory = dict_factory
    c = conn.cursor()
    logger.info("handle_booking")
    payload = request.get_json()

    if request.method == 'GET':
        try:
            # Get query parameters
            firstname =payload['data'].get('firstname')
            lastname = payload['data'].get('lastname')

            if firstname and lastname:
                # Search for specific booking
                c.execute('''
                    SELECT * FROM bookings 
                    WHERE firstname = ? AND lastname = ?
                ''', (firstname, lastname))
            elif firstname:
                # Search by firstname only
                c.execute('''
                    SELECT * FROM bookings 
                    WHERE firstname = ?
                ''', (firstname,))
            elif lastname:
                # Search by lastname only
                c.execute('''
                    SELECT * FROM bookings 
                    WHERE lastname = ?
                ''', (lastname,))
            else:
                # Get all bookings
                c.execute('SELECT * FROM bookings')

            bookings = c.fetchall()
            return jsonify({'bookings': bookings}), 200

        except sqlite3.Error as e:
            return jsonify({'error': str(e)}), 500

        finally:
            conn.close()

    data = request.get_json()

    if request.method == 'POST':
        logger.info("POST")
        try:
            c.execute('''
                INSERT INTO bookings (firstname, lastname, num_people, booking_datetime)
                VALUES (?, ?, ?, ?)
            ''', (data.get('firstname'), data.get('lastname'), data.get('num_people'), data.get('booking_datetime')))
            conn.commit()

            # Get the created booking
            booking_id = c.lastrowid
            c.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,))
            new_booking = c.fetchone()

            return jsonify({'message': 'Booking created successfully', 'booking': new_booking}), 201

        except sqlite3.Error as e:
            return jsonify({'error': str(e)}), 500

    elif request.method == 'PUT':
        try:
            # Check if booking exists
            c.execute('''
                SELECT * FROM bookings 
                WHERE firstname = ? AND lastname = ?
            ''', (data.get('firstname'), data.get('lastname')))

            existing_booking = c.fetchone()

            if not existing_booking:
                return jsonify({'error': 'Booking not found'}), 404

            # Update booking
            c.execute('''
                UPDATE bookings 
                SET num_people = ?, booking_datetime = ?
                WHERE firstname = ? AND lastname = ?
            ''', (data.get('num_people'), data.get('booking_datetime'),
                  data.get('firstname'), data.get('lastname')))
            conn.commit()

            # Get the updated booking
            c.execute('''
                SELECT * FROM bookings 
                WHERE firstname = ? AND lastname = ?
            ''', (data.get('firstname'), data.get('lastname')))
            updated_booking = c.fetchone()

            return jsonify({'message': 'Booking updated successfully', 'booking': updated_booking}), 200

        except sqlite3.Error as e:
            return jsonify({'error': str(e)}), 500

        finally:
            conn.close()


if __name__ == '__main__':
    app.run(debug=True, port=5001)