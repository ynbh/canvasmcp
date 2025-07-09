import { z } from 'zod';
import { generateText, tool } from 'ai';

import { google } from "@ai-sdk/google"

const model = google("models/gemini-2.0-flash-exp")


const weatherTool = tool({
      description: 'Get the weather in a location',
      parameters: z.object({
        location: z.string().describe('The location to get the weather for'),
      }),
      execute: async ({ location }) => ({
        location,
        temperature: 72 + Math.floor(Math.random() * 21) - 10,
      }),
      
    })

const {text, steps} = await generateText({
  model: model,
  tools: {
    weather: weatherTool ,
  },
  prompt: 'What is the weather in San Francisco?',
  maxSteps: 5,
});

console.log(steps)
console.log(text)
