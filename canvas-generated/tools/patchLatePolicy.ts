
import { tool } from "ai";
import { patchLatePolicyDataSchema } from "./aitm.schema.ts";
import { patchLatePolicy, PatchLatePolicyData } from "..";

export default tool({
  description: `
  Patch a late policy
Patch a late policy. No body is returned upon success.
    `,
  parameters: patchLatePolicyDataSchema.omit({ url: true }),
  execute: async (args : Omit<PatchLatePolicyData, "url"> ) => {
    try {
      const { data } = await patchLatePolicy(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    