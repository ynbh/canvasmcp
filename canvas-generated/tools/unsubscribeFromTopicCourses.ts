
import { tool } from "ai";
import { unsubscribeFromTopicCoursesDataSchema } from "./aitm.schema.ts";
import { unsubscribeFromTopicCourses, UnsubscribeFromTopicCoursesData } from "..";

export default tool({
  description: `
  Unsubscribe from a topic
Unsubscribe from a topic to stop receiving notifications about new
entries

On success, the response will be 204 No Content with an empty body
    `,
  parameters: unsubscribeFromTopicCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<UnsubscribeFromTopicCoursesData, "url"> ) => {
    try {
      const { data } = await unsubscribeFromTopicCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    