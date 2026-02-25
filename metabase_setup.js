const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    // Navigate to localhost:3000
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
    
    console.log('📍 Page URL:', page.url());
    console.log('📍 Page title:', await page.title());
    
    // Wait a moment for page to fully load
    await page.waitForTimeout(2000);
    
    // Get page content to see what's happening
    const bodyText = await page.locator('body').textContent();
    console.log('📄 Page contains setup form:', bodyText.includes('name') || bodyText.includes('Admin'));
    
    // Find all inputs
    const inputs = await page.locator('input').all();
    console.log('📝 Found', inputs.length, 'input fields');
    
    // Fill inputs by position
    if (inputs.length >= 1) {
      await inputs[0].fill('Admin');
      console.log('✓ Filled input[0]: Admin');
    }
    
    if (inputs.length >= 2) {
      await inputs[1].fill('admin@example.com');
      console.log('✓ Filled input[1]: admin@example.com');
    }
    
    if (inputs.length >= 3) {
      await inputs[2].fill('admin123456');
      console.log('✓ Filled input[2]: admin123456');
    }
    
    if (inputs.length >= 4) {
      await inputs[3].fill('OSS Analytics');
      console.log('✓ Filled input[3]: OSS Analytics');
    }
    
    // Take screenshot
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'metabase_setup_form.png' });
    console.log('📸 Screenshot saved: metabase_setup_form.png');
    
    // Look for finish/next button
    const buttons = await page.locator('button').all();
    console.log('🔘 Found', buttons.length, 'buttons');
    
    for (let i = 0; i < buttons.length; i++) {
      const text = await buttons[i].textContent();
      console.log(`Button ${i}: "${text}"`);
    }
    
    // Click the last button or first prominent one
    if (buttons.length > 0) {
      const lastButton = buttons[buttons.length - 1];
      const lastButtonText = await lastButton.textContent();
      console.log('Clicking button:', lastButtonText);
      await lastButton.click();
      
      // Wait for navigation
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(2000);
      
      // Take final screenshot
      await page.screenshot({ path: 'metabase_after_click.png' });
      console.log('📸 Screenshot saved: metabase_after_click.png');
      console.log('📍 Final URL:', page.url());
      console.log('✅ Button clicked successfully!');
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    console.error('Stack:', error.stack);
  } finally {
    // Keep browser open for 3 seconds
    await page.waitForTimeout(3000);
    await browser.close();
  }
})();
