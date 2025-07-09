
import { tool } from "ai";
import { getCustomColorsDataSchema } from "./aitm.schema.ts";
import { getCustomColors, GetCustomColorsData } from "..";

export default tool({
  description: `
  Get custom colors
Returns all custom colors that have been saved for a user.
    `,
  parameters: getCustomColorsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetCustomColorsData, "url"> ) => {
    try {
      const { data } = await getCustomColors(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    