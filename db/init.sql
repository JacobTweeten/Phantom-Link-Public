-- Switch to the correct database
\c phantomdb;

-- Create Users table if it doesn't exist
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(80) NOT NULL UNIQUE,
  email VARCHAR(120) NOT NULL UNIQUE,
  password VARCHAR(200) NOT NULL,
  confirmation_code VARCHAR(6),
  is_email_verified BOOLEAN DEFAULT FALSE,
  reset_token VARCHAR(256)
);

-- Create Ghosts table if it doesn't exist
CREATE TABLE IF NOT EXISTS ghosts (
  id SERIAL PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  prompt TEXT NOT NULL,
  city VARCHAR(80),
  state VARCHAR(80),
  image_url VARCHAR(200)
);

-- Create Conversations table if it doesn't exist (without foreign key constraint on ghost_id)
CREATE TABLE IF NOT EXISTS conversations (
  id SERIAL PRIMARY KEY,                 -- Unique ID for each conversation
  user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,  -- Reference to the user
  ghost_name VARCHAR(255) NOT NULL,      -- Store the ghost's name directly
  chat_log TEXT NOT NULL,                -- Store the full conversation as text
  location VARCHAR(255),                 -- Store the location (e.g., city, state)
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Timestamp for the conversation
);



-- I want the conversations table to contain the users previous conversations to view. It should store the
-- ghosts name, and it should save the chat, and display the chat. For every conversation I want to store all of this.

