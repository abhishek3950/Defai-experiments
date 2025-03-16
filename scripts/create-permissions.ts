import { allow } from "zodiac-roles-sdk/kit";
import { processPermissions, Permission, coercePermission } from "zodiac-roles-sdk";
import { writeFileSync, mkdirSync, existsSync } from 'fs';
import { join } from 'path';

// Define addresses
const ZERO_ADDRESS = "0x0000000000000000000000000000000000000000";
const MAX_UINT = "115792089237316195423570985008687907853269984665640564039457584007913129639935";
const ETH_ADDRESS = "0x4200000000000000000000000000000000000006";
const USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913";
const UNIV3_ROUTER = "0x2626664c2603336E57B271c5C0b26F421741e481";
const UNIV3_NFT_MANAGER = "0x03a520b32C04BF3bEEf7BEb72E919cf822Ed34f1";

// Define ERC20 function selectors
const APPROVE_SELECTOR = "0x095ea7b3";

// Define permissions with one entry per token
const allPermissions = [
  // ETH token permissions
  allow.base.eth.approve(UNIV3_ROUTER),
  
  // USDC token permissions - single entry
  coercePermission({
    targetAddress: USDC_ADDRESS,
    functionSelector: APPROVE_SELECTOR,
    params: [UNIV3_ROUTER]
  })
];

// Process permissions and generate targets
const { targets } = processPermissions(allPermissions);

console.log('Generated targets:', targets);

// Ensure directory exists
const dir = './presets/default';
if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true });
}

// Write to permissions.json
const filePath = join(dir, 'permissions.json');
writeFileSync(filePath, JSON.stringify(targets, null, 2));
console.log(`Permissions written to ${filePath}`);