
import { tool } from "ai";
import { getCourseLevelParticipationDataDataSchema } from "./aitm.schema.ts";
import { getCourseLevelParticipationData, GetCourseLevelParticipationDataData } from "..";

export default tool({
  description: `
  Get course-level participation data
Returns page view hits and participation numbers grouped by day
through the
entire history of the course. Page views is returned as a hash, where the
hash keys are
dates in the format "YYYY-MM-DD". The page_views result set
includes page views broken out by access
category. Participations is
returned as an array of dates in the format "YYYY-MM-DD".
    `,
  parameters: getCourseLevelParticipationDataDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetCourseLevelParticipationDataData, "url"> ) => {
    try {
      const { data } = await getCourseLevelParticipationData(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    