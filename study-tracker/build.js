#!/usr/bin/env node
/**
 * Build script - Scans all markdown study files and generates data.json
 * Run: node build.js
 */

const fs = require('fs');
const path = require('path');

const STUDY_ROOT = path.resolve(__dirname, '..');
const OUTPUT_FILE = path.join(__dirname, 'data.json');

// Folders to scan (relative to STUDY_ROOT)
const SCAN_FOLDERS = [
  'JavaScript/30-Day-JS-Mastery',
  'React/30-Days-React-Mastery-2026',
  'angular',
  'Python',
  'NodeJS',
  'TypeScript',
  'DS',
  'flutter',
  'Dart',
  'API-Design',
  'Database-Scaling',
  'DevOps',
  'Microservices',
  'PostgreSQL',
  'Software Architect',
  'Testing',
  'AI-ML-Engineering',
  'Data-Engineering',
  'Agentic-AI',
  'material'
];

function extractInterviewQuestions(content) {
  const questions = [];
  const lines = content.split('\n');
  let inQuestion = false;
  let currentQ = null;
  let answerLines = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    // Match patterns like "### Q1:", "**Q1:**", "### Question 1"
    const qMatch = line.match(/^#{2,4}\s+(?:Q\d+[:.:]|Question\s+\d+)/i) ||
                   line.match(/^\*\*Q\d+[:.:]/) ||
                   line.match(/^#{2,4}\s+\d+\.\s+/);
    
    if (qMatch) {
      if (currentQ) {
        currentQ.answer = answerLines.join('\n').trim();
        questions.push(currentQ);
      }
      currentQ = { question: line.replace(/^[#*\s]+/, '').trim(), answer: '' };
      answerLines = [];
      inQuestion = true;
    } else if (inQuestion) {
      answerLines.push(line);
    }
  }
  if (currentQ) {
    currentQ.answer = answerLines.join('\n').trim();
    questions.push(currentQ);
  }
  return questions;
}

function getTopicFromPath(filePath) {
  const rel = path.relative(STUDY_ROOT, filePath);
  const parts = rel.split(path.sep);
  return parts[0];
}

function getWeekFromPath(filePath) {
  const rel = path.relative(STUDY_ROOT, filePath);
  const weekMatch = rel.match(/week[_-]?(\d+)/i);
  return weekMatch ? parseInt(weekMatch[1]) : null;
}

function getDayFromFile(filename, content) {
  const dayMatch = filename.match(/day[_-]?(\d+)/i) || 
                   filename.match(/Day[_-]?(\d+)/i);
  if (dayMatch) return parseInt(dayMatch[1]);
  
  // Try from content title
  const titleMatch = content.match(/^#\s+Day\s+(\d+)/m);
  return titleMatch ? parseInt(titleMatch[1]) : null;
}

function scanDirectory(dirPath, topic) {
  const files = [];
  
  if (!fs.existsSync(dirPath)) return files;
  
  const entries = fs.readdirSync(dirPath, { withFileTypes: true });
  
  for (const entry of entries) {
    const fullPath = path.join(dirPath, entry.name);
    
    if (entry.isDirectory()) {
      // Skip hidden dirs and node_modules
      if (entry.name.startsWith('.') || entry.name === 'node_modules') continue;
      files.push(...scanDirectory(fullPath, topic));
    } else if (entry.name.endsWith('.md') && entry.name !== 'README.md') {
      try {
        const content = fs.readFileSync(fullPath, 'utf-8');
        const title = content.match(/^#\s+(.+)/m);
        const relPath = path.relative(STUDY_ROOT, fullPath);
        const day = getDayFromFile(entry.name, content);
        const week = getWeekFromPath(fullPath);
        const questions = extractInterviewQuestions(content);
        
        files.push({
          id: relPath.replace(/[/\\]/g, '_').replace('.md', ''),
          path: relPath,
          topic: topic,
          title: title ? title[1].trim() : entry.name.replace('.md', ''),
          filename: entry.name,
          day: day,
          week: week,
          content: content,
          questions: questions,
          wordCount: content.split(/\s+/).length,
          lineCount: content.split('\n').length
        });
      } catch (err) {
        console.error(`Error reading ${fullPath}: ${err.message}`);
      }
    }
  }
  
  return files;
}

function build() {
  console.log('🔍 Scanning study files...');
  
  const allFiles = [];
  const topicSummary = {};
  
  for (const folder of SCAN_FOLDERS) {
    const dirPath = path.join(STUDY_ROOT, folder);
    if (!fs.existsSync(dirPath)) {
      console.log(`  ⚠️  Skipping ${folder} (not found)`);
      continue;
    }
    
    const topicName = folder.split('/')[0];
    const files = scanDirectory(dirPath, topicName);
    allFiles.push(...files);
    
    topicSummary[topicName] = {
      totalFiles: files.length,
      totalDays: files.filter(f => f.day !== null).length,
      totalQuestions: files.reduce((sum, f) => sum + f.questions.length, 0),
      weeks: [...new Set(files.map(f => f.week).filter(Boolean))].sort((a, b) => a - b)
    };
    
    console.log(`  ✅ ${topicName}: ${files.length} files, ${topicSummary[topicName].totalQuestions} questions`);
  }
  
  // Sort files by topic, week, day
  allFiles.sort((a, b) => {
    if (a.topic !== b.topic) return a.topic.localeCompare(b.topic);
    if (a.week !== b.week) return (a.week || 99) - (b.week || 99);
    return (a.day || 99) - (b.day || 99);
  });
  
  const data = {
    generated: new Date().toISOString(),
    stats: {
      totalFiles: allFiles.length,
      totalTopics: Object.keys(topicSummary).length,
      totalQuestions: allFiles.reduce((sum, f) => sum + f.questions.length, 0),
      totalWords: allFiles.reduce((sum, f) => sum + f.wordCount, 0)
    },
    topics: topicSummary,
    files: allFiles
  };
  
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(data, null, 2));
  
  console.log(`\n📊 Summary:`);
  console.log(`   Files: ${data.stats.totalFiles}`);
  console.log(`   Topics: ${data.stats.totalTopics}`);
  console.log(`   Questions: ${data.stats.totalQuestions}`);
  console.log(`   Words: ${data.stats.totalWords.toLocaleString()}`);
  console.log(`\n✅ Generated ${OUTPUT_FILE}`);
}

build();
