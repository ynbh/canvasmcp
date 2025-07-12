import { tool } from "ai";
import { z } from "zod";

export default tool({
  description: `
  Get current date and time
Returns the current date and time for filtering assignments and calendar events by due dates.
    `,
  parameters: z.object({}),
  execute: async () => {
    try {
      const now = new Date();
      return {
        currentDate: now.toISOString(),
        currentDateFormatted: now.toLocaleDateString(),
        currentTime: now.toLocaleTimeString(),
        dayOfWeek: now.toLocaleDateString('en-US', { weekday: 'long' }),
        weekStart: new Date(now.getTime() - now.getDay() * 24 * 60 * 60 * 1000).toISOString(),
        weekEnd: new Date(now.getTime() + (6 - now.getDay()) * 24 * 60 * 60 * 1000).toISOString()
      };
    } catch (e: unknown) {
      console.log(e);
      return "Could not get current date";
    }
  },
});