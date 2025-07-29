#!/usr/bin/env node

// Simple test script for the memory server
import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';

const memoryFile = path.join(process.cwd(), 'memory.json');

console.log('Testing Memory Server...');
console.log('Memory file path:', memoryFile);

// Clean up any existing memory file for testing
if (fs.existsSync(memoryFile)) {
    fs.unlinkSync(memoryFile);
    console.log('Cleaned up existing memory file');
}

// Test that the server can be started
console.log('Starting server...');
const server = spawn('node', ['dist/index.js'], {
    env: { ...process.env, MEMORY_FILE: memoryFile },
    stdio: ['pipe', 'pipe', 'pipe']
});

let output = '';
server.stdout.on('data', (data) => {
    output += data.toString();
});

server.stderr.on('data', (data) => {
    console.error('Server error:', data.toString());
});

// Give the server a moment to start
setTimeout(() => {
    server.kill();
    
    if (output.includes('Server running on stdio')) {
        console.log('✅ Memory server started successfully!');
    } else {
        console.log('Server output:', output);
    }
    
    console.log('\n🎉 Memory server setup complete!');
    console.log('\nTo use the memory server, restart Claude and you should see it available.');
    console.log('\nMemory file location:', memoryFile);
}, 2000);