
import { tool } from "ai";
import { getUserInACourseLevelParticipationDataDataSchema } from "./aitm.schema.ts";
import { getUserInACourseLevelParticipationData, GetUserInACourseLevelParticipationDataData } from "..";

export default tool({
  description: `
  Get user-in-a-course-level participation data
Returns page view hits grouped by hour, and
participation details through the
entire history of the course.

`page_views` are returned as a
hash, where the keys are iso8601 dates, bucketed by the hour.
`participations` are returned as an
array of hashes, sorted oldest to newest.
    `,
  parameters: getUserInACourseLevelParticipationDataDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetUserInACourseLevelParticipationDataData, "url"> ) => {
    try {
      const { data } = await getUserInACourseLevelParticipationData(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    