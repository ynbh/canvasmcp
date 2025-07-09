
import { tool } from "ai";
import { getCustomColorDataSchema } from "./aitm.schema.ts";
import { getCustomColor, GetCustomColorData } from "..";

export default tool({
  description: `
  Get custom color
Returns the custom colors that have been saved for a user for a given context.

The
asset_string parameter should be in the format 'context_id', for example
'course_42'.
    `,
  parameters: getCustomColorDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetCustomColorData, "url"> ) => {
    try {
      const { data } = await getCustomColor(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    