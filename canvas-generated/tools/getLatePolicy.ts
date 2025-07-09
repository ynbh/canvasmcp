
import { tool } from "ai";
import { getLatePolicyDataSchema } from "./aitm.schema.ts";
import { getLatePolicy, GetLatePolicyData } from "..";

export default tool({
  description: `
  Get a late policy
Returns the late policy for a course.
    `,
  parameters: getLatePolicyDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetLatePolicyData, "url"> ) => {
    try {
      const { data } = await getLatePolicy(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    