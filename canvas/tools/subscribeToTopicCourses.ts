
import { tool } from "ai";
import { subscribeToTopicCoursesDataSchema } from "./aitm.schema.ts";
import { subscribeToTopicCourses, SubscribeToTopicCoursesData } from "..";

export default tool({
  description: `
  Subscribe to a topic
Subscribe to a topic to receive notifications about new entries

On success,
the response will be 204 No Content with an empty body
    `,
  parameters: subscribeToTopicCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<SubscribeToTopicCoursesData, "url"> ) => {
    try {
      const { data } = await subscribeToTopicCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    