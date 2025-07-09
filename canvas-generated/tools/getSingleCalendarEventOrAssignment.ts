
import { tool } from "ai";
import { getSingleCalendarEventOrAssignmentDataSchema } from "./aitm.schema.ts";
import { getSingleCalendarEventOrAssignment, GetSingleCalendarEventOrAssignmentData } from "..";

export default tool({
  description: `
  Get a single calendar event or assignment
    `,
  parameters: getSingleCalendarEventOrAssignmentDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleCalendarEventOrAssignmentData, "url"> ) => {
    try {
      const { data } = await getSingleCalendarEventOrAssignment(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    