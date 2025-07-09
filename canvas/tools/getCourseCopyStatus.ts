
import { tool } from "ai";
import { getCourseCopyStatusDataSchema } from "./aitm.schema.ts";
import { getCourseCopyStatus, GetCourseCopyStatusData } from "..";

export default tool({
  description: `
  Get course copy status
DEPRECATED: Please use the {api:ContentMigrationsController#create Content
Migrations API}

Retrieve the status of a course copy
    `,
  parameters: getCourseCopyStatusDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetCourseCopyStatusData, "url"> ) => {
    try {
      const { data } = await getCourseCopyStatus(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    