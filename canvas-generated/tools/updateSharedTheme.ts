
import { tool } from "ai";
import { updateSharedThemeDataSchema } from "./aitm.schema.ts";
import { updateSharedTheme, UpdateSharedThemeData } from "..";

export default tool({
  description: `
  Update a shared theme
Update the specified shared_brand_config with a new name or to point to a new
brand_config.
Uses same parameters as create.
    `,
  parameters: updateSharedThemeDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateSharedThemeData, "url"> ) => {
    try {
      const { data } = await updateSharedTheme(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    