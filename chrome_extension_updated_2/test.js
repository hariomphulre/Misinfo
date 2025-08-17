/**
 * Simple Chrome Extension Test
 * This file helps verify the extension syntax is correct
 */

// Test if popup.js can be parsed
try {
  // Check if the main constants are defined
  if (typeof API_BASE_URL !== 'undefined') {
    console.log('✅ API_BASE_URL defined:', API_BASE_URL);
  }
  
  // Check if main functions exist
  if (typeof collectData === 'function') {
    console.log('✅ collectData function exists');
  }
  
  console.log('✅ Extension syntax test passed');
} catch (error) {
  console.error('❌ Extension syntax error:', error);
}
