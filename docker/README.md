# 🐳 Docker Setup 🚀

## 🌟 Overview
This directory contains all Docker-related configuration files for the AudioKit AI project.

## 🛠️ Services
- **redis**: 🟥 Redis cache server
- **audiokit_ai**: 🤖 Main application container

## 🚀 Usage
1. 🏗️ Build containers: `docker-compose build`
2. 🚀 Start services: `docker-compose up`
3. 🛑 Stop services: `docker-compose down`

## ⚙️ Configuration
- Environment variables: `.env`
- Volume mounts: 
  - Application code: `/app`
  - Credentials: `/app/credentials.json`

## 🌐 Network
All services are connected through the `ak-network` bridge network.

## ⚠️ Confidentiality Notice
All Docker configurations and related files are proprietary and confidential. Unauthorized use or distribution is strictly prohibited. 