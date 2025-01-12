FROM node:14

WORKDIR /app

# Copy only package.json and package-lock.json to cache dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy the rest of the application code
COPY . .

EXPOSE 3000

# Start the development server
CMD ["npm", "start"]
