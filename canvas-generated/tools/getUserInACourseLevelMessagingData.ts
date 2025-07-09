
import { tool } from "ai";
import { getUserInACourseLevelMessagingDataDataSchema } from "./aitm.schema.ts";
import { getUserInACourseLevelMessagingData, GetUserInACourseLevelMessagingDataData } from "..";

export default tool({
  description: `
  Get user-in-a-course-level messaging data
Returns messaging "hits" grouped by day through the entire
history of the
course. Returns a hash containing the number of instructor-to-student messages,
and
student-to-instructor messages, where the hash keys are dates
in the format "YYYY-MM-DD". Message
hits include Conversation messages and
comments on homework submissions.
    `,
  parameters: getUserInACourseLevelMessagingDataDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetUserInACourseLevelMessagingDataData, "url"> ) => {
    try {
      const { data } = await getUserInACourseLevelMessagingData(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    