
import { tool } from "ai";
import { listFavoriteCoursesDataSchema } from "./aitm.schema.ts";
import { listFavoriteCourses, ListFavoriteCoursesData } from "..";


export default tool({
  description: `
  List favorite courses
Retrieve the paginated list of favorite courses for the current user. If the
user has not chosen
any favorites, then a selection of currently enrolled courses will be
returned.

See the {api:CoursesController#index List courses API} for details on accepted include[]
parameters.
    `,
  parameters: listFavoriteCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListFavoriteCoursesData, "url"> ) => {
    try {
      const { data } = await listFavoriteCourses(args);

      const filtered = data?.map(course => ({
        id: course?.id != null ? course.id.toString() : "",  
        name: course.name,
      }));

      return filtered;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    