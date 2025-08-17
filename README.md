# Building snake-nextjs-socketio: A 10-Week Full-Stack Development Course

## Table of Contents

- [Project Overview](#project-overview)
- [Technology Stack](#technology-stack)
- [Project Architecture](#project-architecture)
- [Key Features](#key-features)
- [Week 1: Project Setup and Monorepo Architecture](#week-1-project-setup-and-monorepo-architecture)
- [Week 2: Next.js Frontend Foundation](#week-2-nextjs-frontend-foundation)
- [Week 3: Python Backend and Game Architecture](#week-3-python-backend-and-game-architecture)
- [Week 4: Socket.IO Real-time Communication](#week-4-socketio-real-time-communication)
- [Week 5: Canvas Rendering and Game Visualization](#week-5-canvas-rendering-and-game-visualization)
- [Week 6: Deep Q-Learning Theory and Implementation](#week-6-deep-q-learning-theory-and-implementation)
- [Week 7: AI Agent Integration and Training](#week-7-ai-agent-integration-and-training)
- [Week 8: Deployment and Advanced Features](#week-8-deployment-and-advanced-features)
- [Assessment and Projects](#assessment-and-projects)

## Project Overview

This course teaches students how to build a modern full-stack web application featuring a personal portfolio website with an integrated AI-powered Snake game. The project demonstrates the integration of multiple cutting-edge technologies and serves as both a personal website and an interactive demonstration of machine learning in action.

### Technology Stack

- **Frontend**: Next.js 15, React 19, TypeScript, Mantine UI
- **Backend**: Python with Socket.IO, asyncio
- **AI/ML**: PyTorch, Deep Q-Learning Network (DQN)
- **Real-time Communication**: WebSockets via Socket.IO
- **Deployment**: Static export-ready Next.js app
- **Monorepo Management**: Yarn workspaces

### Project Architecture

The application follows a monorepo structure with two main applications:

1. **`apps/next-app/`**: A Next.js frontend serving as a personal portfolio website

   - Home page with embedded Snake game canvas
   - About page with personal information
   - Projects showcase page
   - Static file serving for images and documents

2. **`apps/socketio/`**: Python backend server handling game logic and AI
   - Real-time game state management
   - Deep Q-Learning agent for autonomous Snake gameplay
   - WebSocket communication with frontend

### Key Features

- **Interactive AI Snake Game**: Runs continuously in the background of the homepage
- **Real-time Updates**: Game state synchronized between Python backend and React frontend
- **Machine Learning**: DQN agent learns to play Snake autonomously
- **Responsive Design**: Clean, modern UI built with Mantine components
- **Portfolio Integration**: Seamless blend of personal branding and technical demonstration

---

## Week 1: Project Setup and Monorepo Architecture

### Learning Objectives (Week 1)

- Understand monorepo concepts and benefits
- Set up Yarn workspaces
- Configure TypeScript across multiple packages
- Establish project structure and conventions

### Topics Covered (Week 1)

- **Monorepo fundamentals**: Why use a monorepo for this project
- **Yarn workspaces setup**: Package management across multiple apps
- **Project structure planning**: Organizing frontend and backend applications
- **Development environment**: VS Code, extensions, and tooling

### Practical Work (Week 1)

- Initialize the monorepo with `package.json` workspaces configuration
- Create the two main application directories: `next-app` and `socketio`
- Set up shared TypeScript configurations and typing systems
- Configure development scripts and workspace dependencies

### Deliverables (Week 1)

- Working monorepo structure
- Basic package.json files for both applications
- Shared tooling configuration (ESLint, TypeScript)

---

## Week 2: Next.js Frontend Foundation

### Learning Objectives (Week 2)

- Master Next.js 15 app router and file-based routing
- Implement responsive layouts with Mantine UI
- Create reusable React components
- Handle static assets and file serving

### Topics Covered (Week 2)

- **Next.js App Router**: Modern routing with the `app/` directory
- **Mantine UI Setup**: Theme configuration and component library integration
- **Layout Systems**: Root layout, nested layouts, and page structure
- **TypeScript Integration**: Strict typing for React components and props

### Practical Work (Week 2)

- Initialize Next.js application with TypeScript
- Install and configure Mantine UI with custom theme
- Create the root layout with navigation header
- Build the basic page structure (home, about, projects)
- Implement responsive design patterns

### Deliverables (Week 2)

- Functional Next.js application with routing
- Custom Mantine theme implementation
- Responsive header component
- Basic page templates

---

## Week 3: Python Backend and Game Architecture

### Learning Objectives (Week 3)

- Design object-oriented game architecture
- Implement core game mechanics in Python
- Understand separation of concerns in game development
- Create modular, testable code structure

### Topics Covered (Week 3)

- **Game Design Patterns**: Entity-based architecture (Snake, Food, Game)
- **Python Class Design**: Proper use of type hints and methods
- **Game Loop Fundamentals**: State management and update cycles
- **Collision Detection**: Boundary checking and self-collision logic

### Practical Work (Week 3)

- Create `Game` class for overall game state management
- Implement `Snake` class with movement, growth, and collision detection
- Build `Food` class with spawning and consumption logic
- Design the game loop structure and state transitions
- Add proper type annotations throughout

### Deliverables (Week 3)

- Complete game logic classes (Game, Snake, Food)
- Working command-line Snake game
- Unit tests for core game mechanics
- Documentation for game architecture

---

## Week 4: Socket.IO Real-time Communication

### Learning Objectives (Week 4)

- Understand WebSocket communication patterns
- Implement bidirectional client-server communication
- Handle connection management and error scenarios
- Design efficient data serialization

### Topics Covered (Week 4)

- **WebSocket vs HTTP**: When and why to use real-time communication
- **Socket.IO Architecture**: Events, rooms, and namespaces
- **Async Python**: Using asyncio for concurrent operations
- **Data Serialization**: JSON serialization for game state

### Practical Work (Week 4)

- Install and configure Socket.IO for Python backend
- Create WebSocket server with connection handling
- Implement game state broadcasting to connected clients
- Add client-side Socket.IO integration in React
- Handle connection errors and reconnection logic

### Deliverables (Week 4)

- Working Socket.IO server with async Python
- Real-time game state updates between backend and frontend
- Connection management and error handling
- Basic game control from frontend

---

## Week 5: Canvas Rendering and Game Visualization

### Learning Objectives (Week 5)

- Master HTML5 Canvas API for game rendering
- Implement smooth animations and visual effects
- Handle responsive canvas sizing
- Optimize rendering performance

### Topics Covered (Week 5)

- **Canvas Fundamentals**: 2D context, drawing operations
- **Game Rendering Patterns**: Frame-based updates and double buffering
- **Responsive Canvas**: Dynamic sizing and pixel density handling
- **Visual Design**: Color schemes, rounded rectangles, and grid systems

### Practical Work (Week 5)

- Create the game canvas component in React
- Implement grid-based rendering system
- Add smooth shape drawing with rounded rectangles
- Integrate real-time game state visualization
- Implement responsive canvas resizing
- Add visual feedback for game events

### Deliverables (Week 5)

- Functional game canvas with real-time updates
- Smooth visual animations
- Responsive design that works on all screen sizes
- Polished visual design matching the site theme

---

## Week 6: Deep Q-Learning Theory and Implementation

### Learning Objectives (Week 6)

- Understand reinforcement learning concepts
- Implement Deep Q-Networks (DQN) from scratch
- Design reward systems for game AI
- Handle neural network training in real-time

### Topics Covered (Week 6)

- **Reinforcement Learning Basics**: Agents, environments, rewards
- **Q-Learning Algorithm**: Temporal difference learning
- **Deep Neural Networks**: PyTorch implementation for Q-learning
- **Experience Replay**: Memory buffers and batch training

### Practical Work (Week 6)

- Implement the `LinearQNet` neural network architecture
- Create the `QTrainer` class for model training
- Design state representation for Snake game
- Implement reward function for learning optimization
- Add experience replay buffer for stable training

### Deliverables (Week 6)

- Complete DQN implementation with PyTorch
- Working neural network training system
- Reward function design and testing
- Model saving and loading functionality

---

## Week 7: AI Agent Integration and Training

### Learning Objectives (Week 7)

- Integrate AI agent with game loop
- Implement epsilon-greedy exploration strategy
- Handle action space and state space design
- Monitor training progress and performance

### Topics Covered (Week 7)

- **Agent-Environment Interaction**: Action selection and state updates
- **Exploration vs Exploitation**: Epsilon-greedy strategy implementation
- **Training Loops**: Short-term and long-term memory training
- **Performance Metrics**: Score tracking and learning curves

### Practical Work (Week 7)

- Create the `DQN` agent class with action selection
- Implement epsilon-greedy exploration with decay
- Integrate agent decision-making with game controls
- Add training statistics and performance monitoring
- Implement automatic game reset and continuous learning

### Deliverables (Week 7)

- Fully integrated AI agent playing Snake autonomously
- Training statistics and performance monitoring
- Configurable exploration parameters
- Continuous learning system

---

## Week 8: Deployment and Advanced Features

### Learning Objectives (Week 8)

- Deploy applications to production environments
- Implement CI/CD pipelines
- Add advanced features and optimizations
- Plan for scaling and maintenance

### Topics Covered (Week 8)

- **Deployment Strategies**: Static hosting vs server deployment
- **CI/CD Pipelines**: Automated testing and deployment
- **Advanced Features**: Model persistence, game statistics, multiplayer potential
- **Scaling Considerations**: Performance optimization and infrastructure

### Practical Work (Week 8)

- Configure Next.js for static export deployment
- Set up Python server deployment with proper process management
- Implement model persistence and loading for the AI agent
- Add advanced game features (speed control, statistics)
- Create deployment documentation and setup guides
- Plan future enhancements and scaling strategies

### Deliverables (Week 8)

- Fully deployed production applications
- CI/CD pipeline configuration
- Advanced feature implementations
- Comprehensive project documentation
- Future development roadmap

---

## Assessment and Projects

### Weekly Assessments

- **Weeks 1-3**: Project setup and architecture (foundational concepts)
- **Weeks 4-6**: Backend implementation and AI integration (technical depth)
- **Weeks 7-9**: Frontend development and UX design (practical application)
- **Week 10**: Final project presentation and deployment (complete product)

### Final Project Requirements

Students should deliver:

1. Fully functional monorepo with both applications
2. Personal portfolio website with custom content
3. AI Snake game with trained model
4. Production deployment of both applications
5. Comprehensive documentation and presentation

### Extension Opportunities

Advanced students can explore:

- Multiplayer Snake functionality
- Different AI algorithms (A\*, genetic algorithms)
- Mobile responsive optimizations
- Advanced analytics and monitoring
- Custom game modes and features

This course structure provides a comprehensive journey through modern full-stack development while teaching essential concepts in web development, real-time communication, machine learning, and software engineering best practices.
