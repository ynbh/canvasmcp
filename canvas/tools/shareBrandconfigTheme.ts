
import { tool } from "ai";
import { shareBrandconfigThemeDataSchema } from "./aitm.schema.ts";
import { shareBrandconfigTheme, ShareBrandconfigThemeData } from "..";

export default tool({
  description: `
  Share a BrandConfig (Theme)
Create a SharedBrandConfig, which will give the given brand_config a
name
and make it available to other users of this account.
    `,
  parameters: shareBrandconfigThemeDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShareBrandconfigThemeData, "url"> ) => {
    try {
      const { data } = await shareBrandconfigTheme(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    