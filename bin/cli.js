#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const os = require('os');

const SKILLS_DIR = path.resolve(__dirname, '..', 'skills');
const CLAUDE_SKILLS_DIR = path.join(os.homedir(), '.claude', 'skills');

const args = process.argv.slice(2);
const command = args[0];

function listSkills() {
  if (!fs.existsSync(SKILLS_DIR)) {
    console.error('Skills directory not found:', SKILLS_DIR);
    process.exit(1);
  }
  const skills = fs.readdirSync(SKILLS_DIR).filter(d =>
    fs.statSync(path.join(SKILLS_DIR, d)).isDirectory() &&
    fs.existsSync(path.join(SKILLS_DIR, d, 'SKILL.md'))
  );
  if (skills.length === 0) {
    console.log('No skills found.');
    return;
  }
  console.log('\nAvailable skills:\n');
  skills.forEach(name => {
    const content = fs.readFileSync(path.join(SKILLS_DIR, name, 'SKILL.md'), 'utf8');
    const descMatch = content.match(/^description:\s*(.+)$/m);
    const desc = descMatch ? descMatch[1].trim().slice(0, 90) + (descMatch[1].length > 90 ? '…' : '') : '';
    console.log(`  ${name}`);
    if (desc) console.log(`    ${desc}`);
    console.log();
  });
}

function addSkill(skillName) {
  if (!skillName) {
    console.error('Error: --skill <name> is required.');
    printHelp();
    process.exit(1);
  }

  const srcDir = path.join(SKILLS_DIR, skillName);
  if (!fs.existsSync(path.join(srcDir, 'SKILL.md'))) {
    console.error(`Skill not found: "${skillName}"`);
    console.error('Run with "list" to see available skills.');
    process.exit(1);
  }

  const destDir = path.join(CLAUDE_SKILLS_DIR, skillName);
  fs.rmSync(destDir, { recursive: true, force: true });
  fs.cpSync(srcDir, destDir, { recursive: true });

  console.log(`Skill "${skillName}" installed to ${destDir}`);
  console.log('Restart Claude Code to activate it.');
}

function printHelp() {
  console.log(`
claude-skills — Install Claude Code skills from sernafa/claude-skills

Usage:
  claude-skills list                        List available skills
  claude-skills add --skill <name>          Install a skill to ~/.claude/skills/

Examples:
  claude-skills list
  claude-skills add --skill senior-commit-writer

npx usage:
  npx @sernafa/claude-skills list
  npx @sernafa/claude-skills add --skill senior-commit-writer
`);
}

switch (command) {
  case 'list':
    listSkills();
    break;

  case 'add': {
    const skillFlagIdx = args.indexOf('--skill');
    const skillName = skillFlagIdx !== -1 ? args[skillFlagIdx + 1] : undefined;
    addSkill(skillName);
    break;
  }

  case '--help':
  case '-h':
  case undefined:
    printHelp();
    break;

  default:
    console.error(`Unknown command: "${command}"`);
    printHelp();
    process.exit(1);
}
