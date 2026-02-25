const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    // Try the setup route directly
    console.log('🔍 Checking setup route...');
    await page.goto('http://localhost:3000/auth/login', { waitUntil: 'networkidle' });
    console.log('✓ Login page loaded');
    console.log('URL:', page.url());
    
    // Try setup
    await page.goto('http://localhost:3000/setup', { waitUntil: 'networkidle' });
    console.log('✓ Setup page loaded');
    console.log('URL:', page.url());
    
    const title = await page.title();
    console.log('Title:', title);
    
    // Check for setup-specific content
    const bodyText = await page.locator('body').textContent();
    const hasSetupContent = bodyText.includes('Welcome') || bodyText.includes('setup') || bodyText.includes('database');
    console.log('Has setup content:', hasSetupContent);
    
    // Take screenshot
    await page.screenshot({ path: 'metabase_check.png' });
    console.log('Screenshot saved');
    
  } catch (error) {
    console.error('Error:', error.message);
  } finally {
    await page.waitForTimeout(2000);
    await browser.close();
  }
})();
