# ConnectHub Frontend Service

React-based frontend for the ConnectHub chat application.

## 🎯 Features

- **Modern UI**: Built with React 18
- **Client-Side Routing**: React Router for smooth navigation
- **API Integration**: Axios for Flask backend communication
- **Responsive Design**: Works on desktop and mobile
- **Professional Styling**: Glass-morphism effects and gradient themes

## 📁 Project Structure

```
frontend-service/
├── public/
│   └── index.html          # HTML entry point
├── src/
│   ├── pages/              # Page components
│   │   ├── LoginPage.js
│   │   ├── RegisterPage.js
│   │   ├── ChatPage.js
│   │   ├── ProfilePage.js
│   │   └── UsersPage.js
│   ├── services/           # API communication
│   │   └── api.js
│   ├── styles/             # CSS files
│   │   ├── App.css
│   │   ├── ChatPage.css
│   │   └── UsersPage.css
│   ├── App.js              # Main app with routing
│   └── index.js            # React entry point
├── Dockerfile              # Multi-stage Docker build
├── nginx.conf              # Nginx configuration
└── package.json            # Dependencies
```

## 🚀 Development

### Prerequisites
- Node.js 18+
- npm or yarn

### Install Dependencies
```bash
cd frontend-service
npm install
```

### Run Development Server
```bash
npm start
```
Frontend will run at http://localhost:3000

### Build for Production
```bash
npm run build
```
Creates optimized build in `build/` directory

## 🐳 Docker

### Build Image
```bash
docker build -t connecthub-frontend .
```

### Run Container
```bash
docker run -p 3000:80 connecthub-frontend
```

### With Docker Compose
```bash
# From project root
docker-compose up frontend
```

## 🔗 API Endpoints Used

All API calls go through `/api/` proxy to Flask backend:

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/profile` - Get current user
- `GET /api/chat/messages` - Get all messages
- `POST /api/chat/send` - Send message
- `DELETE /api/chat/message/:id` - Delete message
- `GET /api/users` - Get all users

## 🎨 Components Explained

### LoginPage.js
- Handles user authentication
- Stores JWT token in localStorage
- Redirects to chat on success

### RegisterPage.js
- New user registration
- Client-side password validation
- Redirects to login after successful registration

### ChatPage.js
- Main chat interface
- Auto-refreshes messages every 3 seconds
- Real-time message display
- Delete your own messages

### ProfilePage.js
- Display user information
- Shows username, email, join date

### UsersPage.js
- Lists all registered users
- Card-based grid layout
- Avatar generation from username

## 🛠️ Technologies

- **React 18** - UI framework
- **React Router 6** - Client-side routing
- **Axios** - HTTP client
- **Nginx** - Production web server
- **Docker** - Containerization

## 📝 Notes

- API proxy configured in `package.json` for development
- Nginx handles routing in production
- JWT tokens stored in localStorage
- Auto-logout on 401 (unauthorized) responses
