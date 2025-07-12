

import fs from 'fs';
import path from 'path';


export function exportToMD(messages: { role: string, content: string }[]) {

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `session-${timestamp}.md`;
    const fullPath = path.join('conversations', filename);

    const content = messages
        .filter(m => m.role === 'user' || m.role === 'assistant')
        .map(m =>
            m.role === 'user'
                ? `### You:\n${m.content}`
                : `### Assistant:\n${m.content}`
        )
        .join('\n\n---\n\n');

    fs.mkdirSync('conversations', { recursive: true });
    fs.writeFileSync(fullPath, content);

    console.log(`Conversation exported to ${fullPath}`);

    process.exit(0); 
}