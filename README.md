# VeriFace

## Table of Contents
- [Description](#description)
- [Objective](#objective)
- [Collaborators](#Collaborators)
- [Usage](#usage)
- [Requirements](#Requirements)

## Description
VeriFace is a project we are implementing for our senior project in Computer Engineering. It is an attendance tracking system that uses RFID and facial recognition to mark and check attendance easier and more accurate than the traditional method of marking attendance like paper sign-in sheets or manually calling out names in a classroom. These older methods are often time-consuming, prone to erros, and can also be easily manipulated.

The system works with an Arduino board connected with the RFID reader to scan tags and then confirms the identity with facial recognition through the webcam of a laptop for simplicity. Everything is managed through a website that we are building with mainly Flask, Python, and SQLAlchemy, where attedance records can be viewed and managed. The website includes different roles (like guest, student, professor, and admin), and each role has specific privileges to access or perform certain tasks within the system.

## Objective
The goal that we set for this project is to create a simple, reliable, and secure way to track attendance. Instead of relying on manual sign-ins or outdated methods, we want to automate the process and reduce errors during the attendance marking process. It is designed to save time, keep records organized, and make things more transparent for everyone that uses. By adding roles and privileges, we’re making sure the system is flexible and secure, so only the right people can perform certain actions.


## Collaborators
- Rodrigo Chen
- YueYing Lee
- Natalie Leung
- Kenneth Nguyen

## Usage

### Prerequisites
Hardware:
- Arduino Board: Compatible with the MFRC522 RFID module.
- MFRC522 RFID: For reading RFID tags.
- Wires: Jumper wires to connect the Arduino and RFID module.

Software:
- Operating System: Linux (tested environment; other OS may require modifications).
- Python3: Version 3.10.12 or higher.
- Pip3: Python package manager.
- Dependencies: Listed in [Required Dependencies](dependencies.txt)

### Hardware Setup
To set up the hardware for the RFID system:
1. Connect the MFRC522 RFID Module to the Arduino Board. [Refer to this datasheet link](https://www.nxp.com/docs/en/data-sheet/MFRC522.pdf)
2. Upload Code to the Arduino.
3. Verify Connections.
4. Connect the Arduino to the your computer bia USB cable
5. Test RFID reader by running the following Python script:  ``python3 rfid_read.py``

### Python 3 Installation
If you have already installed, you can skip this section.

To check if you already have python3 and pip3 installed or check the version in your system, you can use the following command: ``python3 --version``. If the command is not found, then run ``sudo apt-get install python3``. If the version is older, then run ``sudo apt-get upgrade``

### Instructions
This section provides step-by-step instructions on how to clone the repository from the github, set up the virtual environment, install the required dependencies for this project, and run the application.
1. ``git clone https://github.com/YueYingLee/VeriFace.git``
2. ``cd VeriFace``
3. ``python3 -m venv venv``
4. ``source venv/bin/activate``
5. ``pip3 install -r dependencies.txt``
6. ``python3 run.py``

After running successfully, you can access the web application with the following url: [http://127.0.0.1:5000](http://127.0.0.1:5000)

If you want to exit the virtual environment, run the following command:
``deactivate``

For more information on virtual environment, [visit this website for more information on venv](https://docs.python.org/3/library/venv.html)

### Reinitialize Database
To reinitialize the database, run the following command: ``python3 reset_db.py``

After running this command, all the data stored previsouly will be deleted and a new database file will be created.
