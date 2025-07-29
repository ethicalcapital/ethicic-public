# MCP Servers for Ethical Capital

This directory contains Model Context Protocol (MCP) servers used with Claude for enhanced functionality.

## Memory Server

The memory server provides persistent knowledge graph storage for Claude, allowing it to remember information across conversations.

### Setup

The memory server is automatically configured in your Claude desktop config. It stores data in:
```
mcp-servers/memory/memory.json
```

### Usage

Once configured and Claude is restarted, you can use memory-related commands like:
- Creating entities and relationships
- Adding observations
- Searching the knowledge graph
- Managing persistent information

### Files

- `memory/index.ts` - Main server implementation
- `memory/package.json` - Dependencies and scripts
- `memory/tsconfig.json` - TypeScript configuration
- `memory/start.sh` - Startup script
- `memory/test.js` - Test script
- `memory/README.md` - Detailed memory server documentation

### Development

To rebuild the memory server:
```bash
cd mcp-servers/memory
npm run build
```

To test the server:
```bash
cd mcp-servers/memory
node test.js
```