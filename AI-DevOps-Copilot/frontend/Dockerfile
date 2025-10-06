FROM node:20-bullseye 
 
WORKDIR /app 
 
COPY package.json package-lock.json* ./ 
RUN npm ci 
 
COPY . . 

RUN chmod +x node_modules/.bin/vite
 
EXPOSE 5173 
 
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
