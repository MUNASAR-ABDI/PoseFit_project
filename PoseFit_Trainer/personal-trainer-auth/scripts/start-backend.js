const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Define paths
const rootDir = path.resolve(__dirname, '../..');
const backendDir = path.join(rootDir, 'AI_PersonTrainer backend', 'AI_PersonTrainer_april_10_4_21');
const scriptFile = path.join(backendDir, 'api_server.py');

// Check if the backend file exists
if (!fs.existsSync(scriptFile)) {
  console.error(`Backend API server file not found at ${scriptFile}`);
  process.exit(1);
}

console.log('Starting backend API server...');
console.log(`Backend directory: ${backendDir}`);
console.log(`Script file: ${scriptFile}`);

// Run the Python server with appropriate command
const isWindows = process.platform === 'win32';
const pythonCommand = isWindows ? 'python' : 'python3';

// Start the server
const server = spawn(pythonCommand, [scriptFile], {
  cwd: backendDir,
  stdio: 'inherit', // Show output in the console
});

// Handle server events
server.on('error', (err) => {
  console.error('Failed to start backend server:', err);
});

server.on('exit', (code, signal) => {
  if (code) {
    console.log(`Backend server exited with code ${code}`);
  } else if (signal) {
    console.log(`Backend server was killed with signal ${signal}`);
  } else {
    console.log('Backend server exited normally');
  }
});

// Handle process termination
process.on('SIGINT', () => {
  console.log('Stopping backend server...');
  server.kill('SIGINT');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('Stopping backend server...');
  server.kill('SIGTERM');
  process.exit(0);
});

console.log('Backend server should be running. Press Ctrl+C to stop.'); 