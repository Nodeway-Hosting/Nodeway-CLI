const { execSync } = require('child_process');

/**
 * Post-install script for NPM wrapper.
 * Ensures the 'nodeway' python package is installed.
 */

console.log('\x1b[36m%s\x1b[0m', 'Checking Nodeway CLI dependencies...');

try {
    // Check if 'nodeway' command is available
    execSync('nodeway --version', { stdio: 'ignore' });
    console.log('\x1b[32m%s\x1b[0m', '✔ Nodeway CLI (Python) is already installed.');
} catch (e) {
    console.log('\x1b[33m%s\x1b[0m', '⚠ Nodeway CLI (Python) not found. Attempting to install via pip...');
    
    try {
        // Attempt to install from PyPI
        execSync('pip install nodeway', { stdio: 'inherit' });
        console.log('\x1b[32m%s\x1b[0m', '✔ Successfully installed Nodeway CLI via pip.');
    } catch (err) {
        console.error('\x1b[31m%s\x1b[0m', '✖ Failed to install Nodeway CLI automatically.');
        console.log('Please ensure Python is installed and run:');
        console.log('  pip install nodeway');
        process.exit(0); // Exit gracefully so npm install doesn't fail
    }
}
