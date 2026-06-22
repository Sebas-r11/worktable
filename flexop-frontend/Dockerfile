FROM node:20-alpine

WORKDIR /app

# Copiar archivos de dependencias
COPY package.json package-lock.json* ./

# Instalar dependencias
RUN npm install

# Copiar el resto del proyecto
COPY . .

EXPOSE 3000

# Iniciar servidor de desarrollo con host 0.0.0.0 para acceso desde fuera del contenedor
CMD ["npx", "next", "dev", "-H", "0.0.0.0", "-p", "3000"]
