# Phantom-Link

Phantom-Link is a location-based web application that blends history and technology, enabling users to interact with "ghosts" of historical figures from their area. By leveraging AI and historical data, the application generates engaging, era-appropriate conversations that provide a unique educational and storytelling experience.

## Project Overview

- **Developer**: Jacob Tweeten
- **Status**: In Progress (Capstone Final Project, Completion Expected: May 2025)
- **Technologies Used**:
  - **Frontend**: React
  - **Backend**: Flask
  - **Database**: PostgreSQL
  - **Testing/Deployment**: Docker
  - **Email Verification**: Zoho SMTP
  - **AI Integration**: OpenAI API
- **Purpose**: Explore the intersection of AI and interactive storytelling through historical and cultural education.

## Key Features

- **AI-Powered Conversations**: Generates dynamic dialogues tailored to the personality and profession of historical figures using OpenAI.
- **Location-Based Experience**: Identifies historical figures near the user's location by parsing Wikipedia data.
- **Secure User Accounts**: Includes email verification and a custom database for storing user profiles and interactions.
- **Educational and Entertaining**: Encourages exploration of local history through immersive storytelling.

## Roadmap

- **January - March 2025**: Finalize functionality and optimize AI interactions.
- **April 2025**: Conduct usability testing and refine the user experience.
- **May 2025**: Complete and present as the capstone final project.

## How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/JacobTweeten/Phantom-Link-Public.git
   cd Phantom-Link-Public

   # Setting Up the `docker-compose.yml` File

To successfully run Phantom-Link using Docker, you need to configure the environment variables in the `docker-compose.yml` file. Follow these steps to set up your file:

## Instructions for Environment Variables

### `frontend` Service
No additional setup is required for the `frontend` service. It will automatically use the React app from the `./ui` directory.

---

### `backend` Service
Update the following environment variables under the `backend` service:

- **`OPENAI_API_KEY`**  
  - Replace `<your-openai-api-key>` with your OpenAI API key.
  - Example:
    ```yaml
    - OPENAI_API_KEY=sk-your-openai-key
    ```

- **`FLASK_SECRET_KEY`**  
  - Generate a secure secret key for Flask sessions and replace `<your-flask-secret-key>`.
  - Example:
    ```yaml
    - FLASK_SECRET_KEY=your-secure-key
    ```

- **`SQLALCHEMY_DATABASE_URI`**  
  - Provide the connection string for your PostgreSQL database in the format:  
    `postgresql://<username>:<password>@db:5432/<database_name>`
  - Example:
    ```yaml
    - SQLALCHEMY_DATABASE_URI=postgresql://phantom_user:secure_password@db:5432/phantomdb
    ```

---

### `db` Service
Update the following environment variables under the `db` service:

- **`POSTGRES_DB`**  
  - Set the name of your database.
  - Example:
    ```yaml
    - POSTGRES_DB=phantomdb
    ```

- **`POSTGRES_USER`**  
  - Set the username for your PostgreSQL database.
  - Example:
    ```yaml
    - POSTGRES_USER=phantom_user
    ```

- **`POSTGRES_PASSWORD`**  
  - Set a secure password for the PostgreSQL database.
  - Example:
    ```yaml
    - POSTGRES_PASSWORD=secure_password
    ```

---

## Example Configuration
Here’s an example of the `docker-compose.yml` file after filling out the environment variables:

```yaml
services:
  frontend:
    container_name: phantom-link-ui
    build:
      context: ./ui
    ports:
      - "3000:3000"
    volumes:
      - ./ui:/app
    command: npm start
    depends_on:
      - backend

  backend:
    container_name: phantom-link-backend
    build:
      context: ./backend
    ports:
      - "5000:5000"
    environment:
      - OPENAI_API_KEY=sk-your-openai-key
      - FLASK_SECRET_KEY=your-secure-key
      - SQLALCHEMY_DATABASE_URI=postgresql://phantom_user:secure_password@db:5432/phantomdb
    command: flask run --host=0.0.0.0
    depends_on:
      - db

  db:
    container_name: phantom-link-db
    build:
      context: ./db
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=phantomdb
      - POSTGRES_USER=phantom_user
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  postgres-data:

