
import { tool } from "ai";
import { unShareBrandconfigThemeDataSchema } from "./aitm.schema.ts";
import { unShareBrandconfigTheme, UnShareBrandconfigThemeData } from "..";

export default tool({
  description: `
  Un-share a BrandConfig (Theme)
Delete a SharedBrandConfig, which will unshare it so you nor anyone
else in
your account will see it as an option to pick from.
    `,
  parameters: unShareBrandconfigThemeDataSchema.omit({ url: true }),
  execute: async (args : Omit<UnShareBrandconfigThemeData, "url"> ) => {
    try {
      const { data } = await unShareBrandconfigTheme(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    