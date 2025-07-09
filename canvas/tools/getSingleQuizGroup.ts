
import { tool } from "ai";
import { getSingleQuizGroupDataSchema } from "./aitm.schema.ts";
import { getSingleQuizGroup, GetSingleQuizGroupData } from "..";

export default tool({
  description: `
  Get a single quiz group
Returns details of the quiz group with the given id.
    `,
  parameters: getSingleQuizGroupDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleQuizGroupData, "url"> ) => {
    try {
      const { data } = await getSingleQuizGroup(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    