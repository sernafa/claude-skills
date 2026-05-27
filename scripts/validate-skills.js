#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const SKILLS_DIR = path.resolve(__dirname, '..', 'skills');
const MAX_DESC_LENGTH = 1024;

let errors = 0;
let checked = 0;

function parseFrontmatter(content) {
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return null;
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

function fail(skill, msg) {
  console.error(`  FAIL [${skill}] ${msg}`);
  errors++;
}

function pass(skill, msg) {
  console.log(`  OK   [${skill}] ${msg}`);
}

if (!fs.existsSync(SKILLS_DIR)) {
  console.error('Skills directory not found:', SKILLS_DIR);
  process.exit(1);
}

const dirs = fs.readdirSync(SKILLS_DIR).filter(d =>
  fs.statSync(path.join(SKILLS_DIR, d)).isDirectory()
);

if (dirs.length === 0) {
  console.log('No skill directories found.');
  process.exit(0);
}

console.log('\nValidating skills...\n');

dirs.forEach(name => {
  const skillFile = path.join(SKILLS_DIR, name, 'SKILL.md');
  checked++;

  if (!fs.existsSync(skillFile)) {
    fail(name, 'SKILL.md not found');
    return;
  }

  const content = fs.readFileSync(skillFile, 'utf8');
  const fm = parseFrontmatter(content);

  if (!fm) {
    fail(name, 'YAML frontmatter not found (expected --- block at top of file)');
    return;
  }

  if (!fm.name) {
    fail(name, 'frontmatter missing required field: name');
  } else if (fm.name !== name) {
    fail(name, `frontmatter name "${fm.name}" does not match directory name "${name}"`);
  } else {
    pass(name, `name: ${fm.name}`);
  }

  if (!fm.description) {
    fail(name, 'frontmatter missing required field: description');
  } else if (fm.description.length > MAX_DESC_LENGTH) {
    fail(name, `description exceeds ${MAX_DESC_LENGTH} chars (${fm.description.length} chars)`);
  } else {
    pass(name, `description: ${fm.description.slice(0, 60)}...`);
  }
});

console.log(`\n${checked} skill${checked !== 1 ? 's' : ''} checked. ${errors} error${errors !== 1 ? 's' : ''} found.\n`);
process.exit(errors > 0 ? 1 : 0);
