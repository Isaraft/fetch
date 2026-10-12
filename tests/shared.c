#define FETCH_CODENAME "test"
#define FETCH_ARCH "test"
#define FETCH_OS "test"
#define main fetch_program_main
#include "../fetch.c"
#undef main

static int failures;
#define CHECK(test) do { \
  if (!(test)) { fprintf(stderr, "FAIL line %d: %s\n", __LINE__, #test); failures++; } \
} while (0)

static void test_info_bounds(void) {
  fetch_line_count = 0;
  for (int i = 0; i < F_COUNT; i++) field_line[i] = -1;
  current_field = -1;
  add_line("title");
  add_line("-----");

  char long_value[MAX_LINE_LEN];
  memset(long_value, 'x', sizeof(long_value) - 1);
  long_value[sizeof(long_value) - 1] = '\0';
  for (int i = 0; i < MAX_FETCH_LINES - 2; i++) {
    current_field = i == 0 ? F_UPTIME : F_MEMORY;
    add_info("Long field", "%s", long_value);
  }
  current_field = F_GPU;
  add_info("Dropped", "value");
  CHECK(fetch_line_count == MAX_FETCH_LINES);
  CHECK(field_line[F_GPU] == -1);

  box_wrap_lines();
  CHECK(fetch_line_count == MAX_FETCH_LINES);
  CHECK(field_line[F_UPTIME] == 3);
  CHECK(field_line[F_MEMORY] == -1);
  CHECK(box_width > 0 && box_width <= (MAX_LINE_LEN - 16) / 3);
  CHECK(strstr(fetch_lines[2], "\xe2\x95\xad") == fetch_lines[2]);
  CHECK(strstr(fetch_lines[MAX_FETCH_LINES - 1], "\xe2\x95\xb0") ==
        fetch_lines[MAX_FETCH_LINES - 1]);
  for (int i = 2; i < fetch_line_count; i++) {
    CHECK(memchr(fetch_lines[i], '\0', MAX_LINE_LEN) != NULL);
    CHECK(visible_width(fetch_lines[i]) == box_width + 4);
  }

  is_refresh_pass = 1;
  current_field = F_UPTIME;
  add_info("Uptime", "refreshed");
  CHECK(fetch_line_count == MAX_FETCH_LINES);
  CHECK(strstr(fetch_lines[field_line[F_UPTIME]], "refreshed") != NULL);
  CHECK(visible_width(fetch_lines[field_line[F_UPTIME]]) == box_width + 4);
  is_refresh_pass = 0;
  box_width = 0;
}

static void test_minimal_logos(void) {
  for (int shape = 0; shape < 3; shape++) {
    logo_rows = shape == 2 ? 3 : 1;
    for (int r = 0; r < logo_rows; r++)
      strcpy(logo_data[r], shape == 1 ? "@@@" : "@");
    process_logo();
    POINT_COUNT = 0;
    config_depth = 1.0f;
    depth_user_set = 1;
    build_points();
    CHECK(POINT_COUNT > 0);
    for (int i = 0; i < POINT_COUNT; i++)
      CHECK(isfinite(PX[i]) && isfinite(PY[i]) && isfinite(PZ[i]) &&
            isfinite(NX[i]) && isfinite(NY[i]) && isfinite(NZ[i]));
  }
}

int main(void) {
  test_info_bounds();
  test_minimal_logos();
  printf("Shared unit tests: %s\n", failures ? "FAILED" : "passed");
  return failures ? 1 : 0;
}
