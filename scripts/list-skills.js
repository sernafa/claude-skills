#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const SKILLS_DIR = path.resolve(__dirname, '..', 'skills');

function parseFrontmatter(content) {
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return {};
  const fm = {};
  match[1].split('\n').forEach(line => {
    const sep = line.indexOf(':');
    if (sep === -1) return;
    const key = line.slice(0, sep).trim();
    const val = line.slice(sep + 1).trim();
    fm[key] = val;
  });
  return fm;
}

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
  process.exit(0);
}

const COL_NAME = 28;
const COL_DESC = 70;

console.log('\n' + 'SKILL'.padEnd(COL_NAME) + 'DESCRIPTION');
console.log('-'.repeat(COL_NAME + COL_DESC));

skills.forEach(name => {
  const content = fs.readFileSync(path.join(SKILLS_DIR, name, 'SKILL.md'), 'utf8');
  const fm = parseFrontmatter(content);
  const desc = (fm.description || '').slice(0, COL_DESC - 3);
  const truncated = (fm.description || '').length > COL_DESC - 3 ? desc + '...' : desc;
  console.log(name.padEnd(COL_NAME) + truncated);
});

console.log(`\nTotal: ${skills.length} skill${skills.length !== 1 ? 's' : ''}\n`);
