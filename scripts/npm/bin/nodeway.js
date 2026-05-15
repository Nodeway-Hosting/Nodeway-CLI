#!/usr/bin/env node

/**
 * Nodeway CLI NPM Wrapper
 * This script proxies all commands to the 'nodeway' python package.
 */

const { spawn } = require('child_process');

// Collect arguments passed to 'nodeway'
const args = process.argv.slice(2);

// Execute the 'nodeway' python command
const nodeway = spawn('nodeway', args, { 
    stdio: 'inherit', 
    shell: true 
});

nodeway.on('exit', (code) => {
    process.exit(code || 0);
});

nodeway.on('error', (err) => {
    console.error('Failed to start Nodeway CLI. Make sure you have Python installed and run "pip install nodeway".');
    process.exit(1);
});
