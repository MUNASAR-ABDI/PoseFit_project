/**
 * PoseFit Connection Verification Script
 * 
 * This script checks if all PoseFit components are running and can communicate with each other.
 * Run it after starting all services to ensure proper connectivity.
 */

const http = require('http');

// Configuration - update these values if you've changed the default ports
const components = [
  { name: 'PoseFit Landing Page', url: 'http://localhost:4000', expectStatus: 200 },
  { name: 'PoseFit Trainer', url: 'http://localhost:3000', expectStatus: 200 },
  { name: 'PoseFit Assistant', url: 'http://localhost:3001', expectStatus: 200 },
  { name: 'Backend API', url: 'http://localhost:8002/health', expectStatus: 200 },
];

async function checkEndpoint(endpoint) {
  return new Promise((resolve) => {
    const req = http.get(endpoint.url, (res) => {
      const status = res.statusCode;
      resolve({
        name: endpoint.name,
        url: endpoint.url,
        status,
        success: status === endpoint.expectStatus,
        message: `${status === endpoint.expectStatus ? 'OK' : 'FAILED'} - ${status}`
      });
    });

    req.on('error', (err) => {
      resolve({
        name: endpoint.name,
        url: endpoint.url,
        status: 0,
        success: false,
        message: `ERROR - ${err.message}`
      });
    });

    req.setTimeout(5000, () => {
      req.abort();
      resolve({
        name: endpoint.name,
        url: endpoint.url,
        status: 0,
        success: false,
        message: 'ERROR - Timed out'
      });
    });
  });
}

async function main() {
  console.log('PoseFit Connection Verification');
  console.log('==============================\n');
  
  // Check if components are running
  console.log('Checking component availability...');
  
  const results = await Promise.all(components.map(checkEndpoint));
  
  const allSuccess = results.every(r => r.success);
  
  results.forEach(result => {
    const symbol = result.success ? '✓' : '✗';
    console.log(`${symbol} ${result.name}: ${result.message}`);
  });
  
  if (!allSuccess) {
    console.log('\n⚠️ Some components are not available. Please check if all services are running.');
    console.log('See README.md for instructions on starting all components.');
  } else {
    console.log('\n✅ All components are running correctly.');
    console.log('\nYou can access the PoseFit ecosystem at:');
    console.log('* Landing Page: http://localhost:4000');
    console.log('* PoseFit Trainer: http://localhost:3000');
    console.log('* PoseFit Assistant: http://localhost:3001');
    console.log('* Backend API Docs: http://localhost:8002/api/docs');
  }
}

main().catch(err => {
  console.error('Error running checks:', err);
  process.exit(1);
});
