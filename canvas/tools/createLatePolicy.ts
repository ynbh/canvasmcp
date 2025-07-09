
import { tool } from "ai";
import { createLatePolicyDataSchema } from "./aitm.schema.ts";
import { createLatePolicy, CreateLatePolicyData } from "..";

export default tool({
  description: `
  Create a late policy
Create a late policy. If the course already has a late policy, a
bad_request is
returned since there can only be one late policy
per course.
    `,
  parameters: createLatePolicyDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateLatePolicyData, "url"> ) => {
    try {
      const { data } = await createLatePolicy(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    