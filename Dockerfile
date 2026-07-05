# Stage 1: Build the React Frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend source
COPY frontend/package.json ./
# Instead of installing, we'll just install vite manually for the build if there is no package-lock.json
# Or we can just run npm install since package.json has everything
RUN npm install

COPY frontend/ ./
RUN npm run build


# Stage 2: Serve with FastAPI
FROM python:3.11-slim

WORKDIR /app

# Copy backend requirements and install
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend source
COPY backend/ ./backend/

# Copy built frontend from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose port (Cloud Run defaults to 8080)
ENV PORT=8080
EXPOSE $PORT

# Start FastAPI server
CMD uvicorn backend.main:app --host 0.0.0.0 --port $PORT
