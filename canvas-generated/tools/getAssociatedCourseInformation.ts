
import { tool } from "ai";
import { getAssociatedCourseInformationDataSchema } from "./aitm.schema.ts";
import { getAssociatedCourseInformation, GetAssociatedCourseInformationData } from "..";

export default tool({
  description: `
  Get associated course information
Returns a list of courses that are configured to receive updates
from this blueprint
    `,
  parameters: getAssociatedCourseInformationDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetAssociatedCourseInformationData, "url"> ) => {
    try {
      const { data } = await getAssociatedCourseInformation(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    