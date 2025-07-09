
import { tool } from "ai";
import { getSingleTopicCoursesDataSchema } from "./aitm.schema.ts";
import { getSingleTopicCourses, GetSingleTopicCoursesData } from "..";

export default tool({
  description: `
  Get a single topic
Returns data on an individual discussion topic. See the List action for the
response formatting.
    `,
  parameters: getSingleTopicCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleTopicCoursesData, "url"> ) => {
    try {
      const { data } = await getSingleTopicCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    