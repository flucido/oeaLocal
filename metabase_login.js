const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    // Navigate to login
    await page.goto('http://localhost:3000/auth/login', { waitUntil: 'networkidle' });
    console.log('📍 At login page:', page.url());
    
    // Get the email and password fields
    const emailInput = page.locator('input[type="email"], input[placeholder*="email"], input[name*="email"]').first();
    const passwordInput = page.locator('input[type="password"], input[placeholder*="password"], input[name*="password"]').first();
    
    console.log('Filling credentials...');
    await emailInput.fill('admin@example.com');
    await passwordInput.fill('admin123456');
    console.log('✓ Filled email and password');
    
    // Find and click login button
    const loginButton = page.locator('button:has-text("Sign in"), button:has-text("Login"), button[type="submit"]').first();
    await loginButton.click();
    console.log('✓ Clicked login button');
    
    // Wait for navigation
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Check result
    const finalUrl = page.url();
    console.log('📍 Final URL:', finalUrl);
    const title = await page.title();
    console.log('📄 Page title:', title);
    
    // Take screenshot
    await page.screenshot({ path: 'metabase_logged_in.png' });
    console.log('📸 Screenshot saved: metabase_logged_in.png');
    
    if (finalUrl.includes('dashboard') || finalUrl === 'http://localhost:3000/' || !finalUrl.includes('login')) {
      console.log('✅ Successfully logged in!');
    } else {
      console.log('⚠️ Still on login page or error occurred');
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    await page.waitForTimeout(3000);
    await browser.close();
  }
})();
