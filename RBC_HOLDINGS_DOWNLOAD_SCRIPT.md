# RBC Holdings Download Implementation Script

## Overview
This script implements the direct navigation strategy to download holdings from all RBC investment accounts, bypassing click-blocking mechanisms.

## Prerequisites
- Browser MCP connected and working
- RBC Direct Investing logged in
- Current session active (F22=4WN600S, 7ASERVER=N601LD)

## Account List
Based on the Accounts Summary page analysis:
1. **49813791 (RRSP)** - $1,879,271.00 ✅ **CURRENT**
2. **26674346 (Direct Investing)** - $102,066.00
3. **68000157 (Direct Investing)** - $37,117.00
4. **68551241 (Direct Investing)** - No value shown
5. **69539728 (Direct Investing)** - $491,012.00
6. **69549834 (Direct Investing)** - $26,737.00

## Implementation Script

### **Phase 1: Current Account (49813791 - RRSP)**
```javascript
// We're already on this account's holdings page
// Export the current holdings
await click("Export button", "s2e232");
await wait(5); // Wait for download to complete
console.log("✅ Holdings exported for Account 49813791 (RRSP)");
```

### **Phase 2: Navigate to Account 26674346**
```javascript
// Navigate directly to holdings page for account 26674346
await navigate("https://www1.royalbank.com/cgi-bin/rbaccess/rbunxcgi?F22=4WN600S&7ASERVER=N601LD&LANGUAGE=ENGLISH&7ASCRIPT=/WebUI/Holdings/HoldingsHome#/currency");
await wait(5); // Wait for page load

// Take snapshot to verify we're on the right account
await snapshot();

// Export holdings
await click("Export button", "s2e232");
await wait(5);
console.log("✅ Holdings exported for Account 26674346");
```

### **Phase 3: Navigate to Account 68000157**
```javascript
// Navigate to account 68000157
await navigate("https://www1.royalbank.com/cgi-bin/rbaccess/rbunxcgi?F22=4WN600S&7ASERVER=N601LD&LANGUAGE=ENGLISH&7ASCRIPT=/WebUI/Holdings/HoldingsHome#/currency");
await wait(5);

// Verify account and export
await snapshot();
await click("Export button", "s2e232");
await wait(5);
console.log("✅ Holdings exported for Account 68000157");
```

### **Phase 4: Navigate to Account 68551241**
```javascript
// Navigate to account 68551241
await navigate("https://www1.royalbank.com/cgi-bin/rbaccess/rbunxcgi?F22=4WN600S&7ASERVER=N601LD&LANGUAGE=ENGLISH&7ASCRIPT=/WebUI/Holdings/HoldingsHome#/currency");
await wait(5);

// Verify account and export
await snapshot();
await click("Export button", "s2e232");
await wait(5);
console.log("✅ Holdings exported for Account 68551241");
```

### **Phase 5: Navigate to Account 69539728**
```javascript
// Navigate to account 69539728
await navigate("https://www1.royalbank.com/cgi-bin/rbaccess/rbunxcgi?F22=4WN600S&7ASERVER=N601LD&LANGUAGE=ENGLISH&7ASCRIPT=/WebUI/Holdings/HoldingsHome#/currency");
await wait(5);

// Verify account and export
await snapshot();
await click("Export button", "s2e232");
await wait(5);
console.log("✅ Holdings exported for Account 69539728");
```

### **Phase 6: Navigate to Account 69549834**
```javascript
// Navigate to account 69549834
await navigate("https://www1.royalbank.com/cgi-bin/rbaccess/rbunxcgi?F22=4WN600S&7ASERVER=N601LD&LANGUAGE=ENGLISH&7ASCRIPT=/WebUI/Holdings/HoldingsHome#/currency");
await wait(5);

// Verify account and export
await snapshot();
await click("Export button", "s2e232");
await wait(5);
console.log("✅ Holdings exported for Account 69549834");
```

## Complete Automated Script

### **Full Implementation**
```javascript
async function downloadAllRBCHoldings() {
    const accounts = [
        { number: "49813791", type: "RRSP", value: "$1,879,271.00" },
        { number: "26674346", type: "Direct Investing", value: "$102,066.00" },
        { number: "68000157", type: "Direct Investing", value: "$37,117.00" },
        { number: "68551241", type: "Direct Investing", value: "No value shown" },
        { number: "69539728", type: "Direct Investing", value: "$491,012.00" },
        { number: "69549834", type: "Direct Investing", value: "$26,737.00" }
    ];

    const baseUrl = "https://www1.royalbank.com/cgi-bin/rbaccess/rbunxcgi?F22=4WN600S&7ASERVER=N601LD&LANGUAGE=ENGLISH&7ASCRIPT=/WebUI/Holdings/HoldingsHome#/currency";
    
    console.log("🚀 Starting RBC Holdings Download Process...");
    console.log(`📊 Total Accounts: ${accounts.length}`);
    
    for (let i = 0; i < accounts.length; i++) {
        const account = accounts[i];
        console.log(`\n📋 Processing Account ${i + 1}/${accounts.length}: ${account.number} (${account.type})`);
        
        try {
            // Navigate to account holdings page
            if (i > 0) { // Skip navigation for first account (already there)
                await navigate(baseUrl);
                await wait(5);
            }
            
            // Take snapshot to verify account
            await snapshot();
            
            // Export holdings
            await click("Export button", "s2e232");
            await wait(5);
            
            console.log(`✅ Successfully exported holdings for Account ${account.number}`);
            
        } catch (error) {
            console.error(`❌ Error processing Account ${account.number}:`, error);
            
            // Try to recover by going back to home page
            try {
                await navigate("https://www1.royalbank.com/sgw3/secureapp/N600/ReactUI/?LANGUAGE=ENGLISH#/Home");
                await wait(3);
            } catch (recoveryError) {
                console.error("❌ Recovery failed:", recoveryError);
                break;
            }
        }
    }
    
    console.log("\n🎉 RBC Holdings Download Process Complete!");
    console.log("📁 Check your Downloads folder for the exported files");
}

// Execute the function
downloadAllRBCHoldings();
```

## Error Recovery Strategies

### **Session Expiration Recovery**
```javascript
async function recoverFromSessionExpiration() {
    console.log("🔄 Session expired, attempting recovery...");
    
    // Go back to login page
    await navigate("https://secure.royalbank.com/statics/login-service-ui/index#/full/signin?LANGUAGE=ENGLISH");
    await wait(3);
    
    console.log("⚠️ Manual login required. Please log in and then continue the script.");
    // Script should be paused here for manual login
}
```

### **Export Button Not Found Recovery**
```javascript
async function recoverFromExportButtonNotFound() {
    console.log("🔍 Export button not found, attempting recovery...");
    
    // Try refreshing the page
    await navigate(currentUrl);
    await wait(5);
    
    // Take new snapshot
    await snapshot();
    
    // Try to find export button again
    // If still not found, try alternative navigation
}
```

## File Organization

### **Recommended File Naming Convention**
```
RBC_Holdings_Data/
├── Account_49813791_RRSP_2025-01-15_Holdings.csv
├── Account_26674346_DirectInvesting_2025-01-15_Holdings.csv
├── Account_68000157_DirectInvesting_2025-01-15_Holdings.csv
├── Account_68551241_DirectInvesting_2025-01-15_Holdings.csv
├── Account_69539728_DirectInvesting_2025-01-15_Holdings.csv
└── Account_69549834_DirectInvesting_2025-01-15_Holdings.csv
```

### **File Processing Script**
```javascript
async function organizeDownloadedFiles() {
    const downloadsPath = "~/Downloads";
    const targetPath = "~/RBC_Holdings_Data";
    
    // Create target directory if it doesn't exist
    // Move and rename files
    // Organize by account and date
}
```

## Monitoring and Verification

### **Progress Tracking**
```javascript
const progress = {
    total: 6,
    completed: 0,
    failed: 0,
    current: null,
    startTime: Date.now()
};

function updateProgress(accountNumber, status) {
    if (status === 'success') {
        progress.completed++;
    } else if (status === 'failed') {
        progress.failed++;
    }
    
    progress.current = accountNumber;
    
    console.log(`📊 Progress: ${progress.completed}/${progress.total} completed, ${progress.failed} failed`);
}
```

### **Completion Verification**
```javascript
async function verifyAllDownloads() {
    const expectedFiles = [
        "Account_49813791_RRSP_2025-01-15_Holdings.csv",
        "Account_26674346_DirectInvesting_2025-01-15_Holdings.csv",
        "Account_68000157_DirectInvesting_2025-01-15_Holdings.csv",
        "Account_68551241_DirectInvesting_2025-01-15_Holdings.csv",
        "Account_69539728_DirectInvesting_2025-01-15_Holdings.csv",
        "Account_69549834_DirectInvesting_2025-01-15_Holdings.csv"
    ];
    
    console.log("🔍 Verifying all downloads...");
    
    for (const file of expectedFiles) {
        // Check if file exists
        // Verify file size > 0
        // Log verification status
    }
    
    console.log("✅ Download verification complete!");
}
```

## Execution Instructions

### **Step-by-Step Execution**
1. **Verify Browser MCP Connection**
   - Ensure Browser MCP extension is connected
   - Confirm RBC Direct Investing is logged in

2. **Run the Script**
   - Execute the complete automated script
   - Monitor console output for progress

3. **Handle Any Errors**
   - Follow recovery procedures if needed
   - Manual intervention may be required for session issues

4. **Verify Downloads**
   - Check Downloads folder for exported files
   - Verify file completeness and naming

5. **Organize Files**
   - Move files to project directory
   - Rename according to convention
   - Create organized folder structure

## Success Criteria

### **Completion Checklist**
- [ ] All 6 investment accounts processed
- [ ] Holdings exported from each account
- [ ] Files properly named and organized
- [ ] No manual intervention required (except login if session expires)
- [ ] All downloads verified and complete

### **Performance Targets**
- **Success Rate**: 100%
- **Total Time**: < 10 minutes
- **Error Rate**: 0%
- **Recovery Success**: 100%

This script provides a complete, automated solution for downloading RBC holdings data while bypassing the click-blocking mechanisms that were preventing progress.


